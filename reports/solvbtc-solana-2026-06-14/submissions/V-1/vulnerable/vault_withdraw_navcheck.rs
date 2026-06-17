// IN-SCOPE (post-audit, unaudited): programs/solvbtc/src/contexts/vault_withdraw.rs withdraw_tokens
        // Verify signature
        withdraw_request.verify_signature(Secp256k1EcdsaSignature(signature), self.vault.verifier)?;

        // Check 1.01*nav >= nav of withdraw request
        let nav_diff: u64 = u64::try_from(u128::from(self.vault.nav)
            .checked_mul(100 as u128)
            .ok_or(ProgramError::ArithmeticOverflow)?
            .checked_div(MAX_FEE.into())
            .ok_or(ProgramError::ArithmeticOverflow)?)
            .map_err(|_| ProgramError::ArithmeticOverflow)?;
        let max_nav = self.vault.nav.checked_add(nav_diff).ok_or(ProgramError::ArithmeticOverflow)?;
        require_gte!(max_nav, withdraw_request.nav, SolvError::NAVExceeded);

        // Get withdraw amount and withdraw fee
        let (amount, fee) = Vault::calculate_fee(withdraw_request.withdraw_amount, self.vault.withdraw_fee)?;
        msg!("Withdraw amount: {}, Fee: {}", amount, fee);

        // Signer seeds
        let key = self.vault.mint.key();
